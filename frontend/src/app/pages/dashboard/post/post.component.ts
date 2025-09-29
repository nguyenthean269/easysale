import { Component, OnInit, NO_ERRORS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzButtonModule } from 'ng-zorro-antd/button';

import { NzMessageService } from 'ng-zorro-antd/message';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzPaginationModule } from 'ng-zorro-antd/pagination';
import { NzSpaceModule } from 'ng-zorro-antd/space';
import { NzTypographyModule } from 'ng-zorro-antd/typography';

import { PostService, Post } from '../../../services/post.service';
import { FacebookService, FacebookPage } from '../../../services/facebook.service';

@Component({
  selector: 'app-post',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    NzCardModule,
    NzTableModule,
    NzButtonModule,
    NzDividerModule,
    NzTagModule,
    NzSpinModule,
    NzPaginationModule,
    NzSpaceModule,
    NzTypographyModule
  ],
  templateUrl: './post.component.html',
  styleUrls: ['./post.component.css'],
  schemas: [NO_ERRORS_SCHEMA]
})
export class PostComponent implements OnInit {
  // Posts data
  posts: Post[] = [];
  selectedPosts: Post[] = [];
  postsLoading = false;
  postsPage = 1;
  postsPageSize = 10;
  postsTotal = 0;

  // Facebook pages data
  facebookPages: FacebookPage[] = [];
  selectedFacebookPages: FacebookPage[] = [];
  facebookPagesLoading = false;
  facebookPagesPage = 1;
  facebookPagesPageSize = 10;
  facebookPagesTotal = 0;

  // Post to Facebook
  postingLoading = false;

  constructor(
    private postService: PostService,
    private facebookService: FacebookService,
    private message: NzMessageService
  ) {}

  ngOnInit(): void {
    this.loadPosts();
    this.loadFacebookPages();
  }

  loadPosts(): void {
    this.postsLoading = true;
    this.postService.getPosts(this.postsPage, this.postsPageSize).subscribe({
      next: (response: any) => {
        this.posts = response.data.posts;
        this.postsTotal = response.data.pagination.total;
        this.postsLoading = false;
      },
      error: (error: any) => {
        console.error('Error loading posts:', error);
        this.message.error('Lỗi khi tải danh sách bài viết');
        this.postsLoading = false;
      }
    });
  }

  loadFacebookPages(): void {
    this.facebookPagesLoading = true;
    this.facebookService.getFacebookPages(this.facebookPagesPage, this.facebookPagesPageSize, 'true').subscribe({
      next: (response: any) => {
        this.facebookPages = response.data.facebook_pages;
        this.facebookPagesTotal = response.data.pagination.total;
        this.facebookPagesLoading = false;
      },
      error: (error: any) => {
        console.error('Error loading Facebook pages:', error);
        this.message.error('Lỗi khi tải danh sách Facebook pages');
        this.facebookPagesLoading = false;
      }
    });
  }

  onPostsPageChange(page: number): void {
    this.postsPage = page;
    this.loadPosts();
  }

  onFacebookPagesPageChange(page: number): void {
    this.facebookPagesPage = page;
    this.loadFacebookPages();
  }

  onPostSelectionChange(checked: boolean, post: Post): void {
    if (checked) {
      this.selectedPosts.push(post);
    } else {
      this.selectedPosts = this.selectedPosts.filter(p => p.id !== post.id);
    }
  }

  onFacebookPageSelectionChange(checked: boolean, page: FacebookPage): void {
    if (checked) {
      this.selectedFacebookPages.push(page);
    } else {
      this.selectedFacebookPages = this.selectedFacebookPages.filter(p => p.id !== page.id);
    }
  }

  onAllPostsSelectionChange(checked: boolean): void {
    if (checked) {
      this.selectedPosts = [...this.posts];
    } else {
      this.selectedPosts = [];
    }
  }

  onAllFacebookPagesSelectionChange(checked: boolean): void {
    if (checked) {
      this.selectedFacebookPages = [...this.facebookPages];
    } else {
      this.selectedFacebookPages = [];
    }
  }

  onAllPostsSelectionChangeEvent(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.onAllPostsSelectionChange(checked);
  }

  onPostSelectionChangeEvent(event: Event, post: Post): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.onPostSelectionChange(checked, post);
  }

  onAllFacebookPagesSelectionChangeEvent(event: Event): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.onAllFacebookPagesSelectionChange(checked);
  }

  onFacebookPageSelectionChangeEvent(event: Event, page: FacebookPage): void {
    const checked = (event.target as HTMLInputElement).checked;
    this.onFacebookPageSelectionChange(checked, page);
  }

  isPostSelected(post: Post): boolean {
    return this.selectedPosts.some(p => p.id === post.id);
  }

  isFacebookPageSelected(page: FacebookPage): boolean {
    return this.selectedFacebookPages.some(p => p.id === page.id);
  }

  postToFacebook(): void {
    if (this.selectedPosts.length === 0) {
      this.message.warning('Vui lòng chọn ít nhất một bài viết');
      return;
    }

    if (this.selectedFacebookPages.length === 0) {
      this.message.warning('Vui lòng chọn ít nhất một Facebook page');
      return;
    }

    this.postingLoading = true;
    const promises: Promise<any>[] = [];

    this.selectedFacebookPages.forEach(page => {
      this.selectedPosts.forEach(post => {
        const postData = {
          message: post.content,
          link: '',
          image_url: ''
        };

        const promise = this.facebookService.createFacebookPost(page.id, postData).toPromise();
        promises.push(promise);
      });
    });

    Promise.all(promises)
      .then(() => {
        this.message.success('Đăng bài thành công!');
        this.resetForm();
      })
      .catch((error) => {
        console.error('Error posting to Facebook:', error);
        this.message.error('Lỗi khi đăng bài lên Facebook');
      })
      .finally(() => {
        this.postingLoading = false;
      });
  }

  resetForm(): void {
    this.selectedPosts = [];
    this.selectedFacebookPages = [];
  }

  getStatusTag(status: string): string {
    return status === 'posted' ? 'success' : 'default';
  }

  getStatusText(status: string): string {
    return status === 'posted' ? 'Đã đăng' : 'Bản nháp';
  }

  getPageStatusTag(status: boolean): string {
    return status ? 'success' : 'error';
  }

  getPageStatusText(status: boolean): string {
    return status ? 'Hoạt động' : 'Tạm dừng';
  }
} 